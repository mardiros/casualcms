import React from "react";
import {
  Box,
  Button,
  Heading,
  Icon,
  Stack,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react";
import { Draft, PartialDraft } from "../../casualcms/domain/model";
import { ApiError } from "../../casualcms/domain/ports";
import { AppConfig, AppContext } from "../../config";

import { useAuth } from "../login/hooks";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import {
  AddIcon,
  ArrowRightIcon,
  DeleteIcon,
  EditIcon,
  ViewIcon,
} from "@chakra-ui/icons";
import { Result } from "neverthrow";
import { Loader } from "../layout/loader";
import { ApiErrorUI } from "../layout/error_api";
import { PageBreadcrumb } from "../layout/breadcrumb";
import { PageDeletePopoverForm } from "./page_delete";

type PageRowProps = {
  page: PartialDraft;
};

type PageListTableProps = {
  parentPath: string | null;
  config: AppConfig;
  token: string;
  curPage: Draft | null;
};

export const PageRow: React.FunctionComponent<PageRowProps> = (
  props: PageRowProps
) => {
  const page = props.page;
  return (
    <Tr>
      <Td>{page.slug}</Td>
      <Td>{page.title}</Td>
      <Td>
        <Link
          to={`/admin/pages/edit?${new URLSearchParams({
            page: page.meta.path,
          })}`}
        >
          <Icon as={EditIcon} marginEnd={2} />
          Edit
        </Link>
      </Td>
      <Td>
        <a href={`${page.meta.path}`}>
          <Icon as={ViewIcon} marginEnd={2} />
          View
        </a>
      </Td>
      <Td>
        <Link
          to={`/admin/pages/?${new URLSearchParams({
            parent: page.meta.path,
          })}`}
          data-testid="View child pages"
        >
          <Icon as={ArrowRightIcon} marginEnd={2} />
        </Link>
      </Td>
    </Tr>
  );
};

type PageListButtonsProps = {
  curPage: Draft | null;
  subPages: PartialDraft[];
};

export const PageListButtons: React.FunctionComponent<PageListButtonsProps> = (
  props: PageListButtonsProps
) => {
  const { curPage, subPages } = props;
  let navigate = useNavigate();
  const qsEdit = curPage
    ? new URLSearchParams({
        page: curPage.meta.path,
      })
    : "";
  const qs = curPage
    ? new URLSearchParams({
        parent: curPage.meta.path,
        type: curPage.meta.type,
      })
    : "";
  return (
    <Stack p={4} spacing={4} direction="row" align="right">
      {qsEdit && (
        <Button
          onClick={() =>
            navigate(`/admin/pages/edit?${qsEdit}`, { replace: true })
          }
          colorScheme="teal"
        >
          <Icon as={EditIcon} marginEnd={2} />
          Edit
        </Button>
      )}

      <Button
        onClick={() => navigate(`/admin/pages/new?${qs}`, { replace: true })}
        colorScheme="teal"
      >
        <Icon as={AddIcon} marginEnd={2} />
        Add new page
      </Button>

      {curPage && subPages.length == 0 && (
        <PageDeletePopoverForm curPage={curPage} />
      )}
    </Stack>
  );
};

export const PageListTable: React.FunctionComponent<PageListTableProps> = (
  props: PageListTableProps
) => {
  const { config, parentPath, token } = props;
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [subPages, setSubPages] = React.useState<PartialDraft[]>([]);
  const [error, setError] = React.useState<ApiError>(null);

  React.useEffect(() => {
    async function loadSubPages() {
      let pages: Result<PartialDraft[], ApiError>;
      pages = await config.api.draft.listDrafts(token, parentPath);
      pages
        .map((pages: PartialDraft[]) => setSubPages(pages))
        .mapErr((err: ApiError) => setError(err)); // FIXME
      setIsLoading(false);
    }
    loadSubPages();
    return function cleanup() {};
  }, [parentPath]);

  if (isLoading) {
    return <Loader label="Loading pages list" />;
  }
  if (error) {
    return <ApiErrorUI error={error} />;
  }
  return (
    <>
      <TableContainer>
        <Table variant="simple">
          <Thead>
            <Tr>
              <Th>Slug</Th>
              <Th>Title</Th>
              <Th>Edit</Th>
              <Th>View</Th>
              <Th>Childs</Th>
            </Tr>
          </Thead>
          <Tbody>
            {subPages.map((page, i) => (
              <PageRow page={page} key={i} />
            ))}
          </Tbody>
        </Table>
      </TableContainer>
      <PageListButtons curPage={props.curPage} subPages={subPages} />
    </>
  );
};

export const PageList: React.FunctionComponent<{}> = () => {
  // console.log("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
  // console.log("# Rendering page list")
  const config = React.useContext(AppContext);
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";
  const [curPage, setCurPage] = React.useState<Draft | null>(null);
  const [error, setError] = React.useState<ApiError>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [params, setParams] = useSearchParams();
  const parentPath = params.get("parent");

  React.useEffect(() => {
    async function loadCurPage() {
      let page: Result<Draft, ApiError>;
      if (parentPath) {
        page = await config.api.draft.showDraft(token, parentPath);
        page
          .map((page: Draft) => setCurPage(page))
          .mapErr((err: ApiError) => setError(err));
      }
      setIsLoading(false);
    }
    loadCurPage();
    return () => {
      setCurPage(null);
      setError(null);
      setIsLoading(true);
    };
  }, [parentPath]);

  if (isLoading) {
    return <Loader label="Loading pages" />;
  }
  return (
    <Box>
      {curPage && <Heading>{curPage.title}</Heading>}
      <PageBreadcrumb page={curPage} />
      <Box>
        <ApiErrorUI error={error} />
        <PageListTable
          config={config}
          token={token}
          parentPath={parentPath}
          curPage={curPage}
        />
      </Box>
    </Box>
  );
};
