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
import { PartialPage } from "../../casualcms/domain/model";
import { ApiError } from "../../casualcms/domain/ports";
import { AppConfig, AppContext } from "../../config";

import { useAuth } from "../login/components";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { AddIcon, ArrowRightIcon, EditIcon, ViewIcon } from "@chakra-ui/icons";
import { Result } from "neverthrow";
import { Loader } from "../loader/components";
import { ApiErrorUI } from "../errorApi/components";

type PageRowProps = {
  page: PartialPage;
};

type PageListTableProps = {
  parentPath: string | null;
  config: AppConfig;
  token: string;
};

export const PageRow: React.FunctionComponent<PageRowProps> = (
  props: PageRowProps
) => {
  const page = props.page;
  return (
    <Tr>
      <Td>{page.title}</Td>
      <Td>
        <Link to={`/admin/page/edit${page.path}`}>
          <Icon as={EditIcon} marginEnd={2} />
          Edit
        </Link>
      </Td>
      <Td>
        <a href={`${page.path}`}>
          <Icon as={ViewIcon} marginEnd={2} />
          View
        </a>
      </Td>
      <Td>
        <Link
          to={`/admin/pages/?${new URLSearchParams({ parent: page.path })}`}
          data-testid="View child pages"
        >
          <Icon as={ArrowRightIcon} marginEnd={2} />
        </Link>
      </Td>
    </Tr>
  );
};

export const PageListTable: React.FunctionComponent<PageListTableProps> = (
  props: PageListTableProps
) => {
  const parentPath = props.parentPath;
  const config = props.config;
  const token = props.token;
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [subPages, setSubPages] = React.useState<PartialPage[]>([]);
  const [error, setError] = React.useState<ApiError>(null);

  React.useEffect(() => {
    async function loadSubPages() {
      let pages: Result<PartialPage[], ApiError>;
      pages = await config.api.page.listPages(token, parentPath);
      pages
        .map((pages: PartialPage[]) => setSubPages(pages))
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
    return (
      <ul>
        {[...error.keys()].map((k) => (
          <li> {error.get(k)} </li>
        ))}
      </ul>
    );
  }
  return (
    <TableContainer>
      <Table variant="simple">
        <Thead>
          <Tr>
            <Th>Page</Th>
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
  );
};

type PageListButtonsProps = {
  curPage: PartialPage | null;
};

export const PageListButtons: React.FunctionComponent<PageListButtonsProps> = (
  props: PageListButtonsProps
) => {
  const curPage = props.curPage;
  let navigate = useNavigate();
  const qs = curPage
    ? new URLSearchParams({ parent: curPage.path, type: curPage.type })
    : "";
  return (
    <Stack p={4} spacing={4} direction="row" align="right">
      <Button
        onClick={() => navigate(`/admin/page/new?${qs}`, { replace: true })}
      >
        <Icon as={AddIcon} marginEnd={2} />
        Add new page
      </Button>
    </Stack>
  );
};

export const PageList: React.FunctionComponent<{}> = () => {
  // console.log("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
  // console.log("# Rendering page list")
  const config = React.useContext(AppContext);
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";
  const [curPage, setCurPage] = React.useState<PartialPage | null>(null);
  const [error, setError] = React.useState<ApiError>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [params, setParams] = useSearchParams();
  const parentPath = params.get("parent");

  React.useEffect(() => {
    async function loadCurPage() {
      setIsLoading(false);
    }
    loadCurPage();
    return function cleanup() {};
  }, [parentPath]);

  React.useEffect(() => {
    async function loadSubPages() {
      let page: Result<PartialPage, ApiError>;
      if (parentPath) {
        page = await config.api.page.showPage(token, parentPath);
        page
          .map((page: PartialPage) => setCurPage(page))
          .mapErr((err: ApiError) => setError(err));
      }
      setIsLoading(false);
    }
    loadSubPages();
    return function cleanup() {};
  }, [parentPath]);

  if (isLoading) {
    return <Loader label="Loading page" />;
  }
  return (
    <Box>
      <Heading>Pages</Heading>
      <Box>
        <ApiErrorUI error={error} />
        <PageListTable config={config} token={token} parentPath={parentPath} />
        <PageListButtons curPage={curPage} />
      </Box>
    </Box>
  );
};
