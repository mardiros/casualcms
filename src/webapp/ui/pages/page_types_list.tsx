import React from "react";
import {
  Box,
  Container,
  Heading,
  Icon,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react";
import { Page, PartialPageType } from "../../casualcms/domain/model";
import { ApiError } from "../../casualcms/domain/ports";
import { AppContext } from "../../config";

import { useAuth } from "../login/hooks";
import { Link, useSearchParams } from "react-router-dom";
import { ChevronRightIcon } from "@chakra-ui/icons";
import { Loader } from "../layout/loader";
import { ApiErrorUI } from "../layout/error_api";
import { PageBreadcrumb } from "../layout/breadcrumb";

type PageTypesTableProps = {
  isLoading: boolean;
  parentPath: string | null;
  pageTypes: PartialPageType[];
};
export const PageTypesTable: React.FunctionComponent<PageTypesTableProps> = (
  props: PageTypesTableProps
) => {
  if (props.isLoading) {
    return <Loader label="loading page types..." />;
  }

  const pageTypes = props.pageTypes;
  const qs = props.parentPath
    ? new URLSearchParams({ parent: props.parentPath })
    : "";
  return (
    <TableContainer>
      <Table variant="simple">
        <Thead>
          <Tr>
            <Th>Page Type</Th>
          </Tr>
        </Thead>
        <Tbody>
          {pageTypes.map((tpl, i) => (
            <Tr key={i}>
              <Td>
                <Link to={`/admin/page/new/${tpl.type}?${qs}`}>
                  <Icon as={ChevronRightIcon} w={6} h={6} />
                  {tpl.type}
                </Link>
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </TableContainer>
  );
};

export const PageTypeList: React.FunctionComponent<{}> = () => {
  const config = React.useContext(AppContext);
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [pageTypes, setTemplates] = React.useState<PartialPageType[]>([]);
  const [error, setError] = React.useState<ApiError>(null);
  const [params, setParams] = useSearchParams();
  const parentType = params.get("type");
  const parentPath = params.get("parent");
  const [parentPage, setParentPage] = React.useState<Page | null>(null);

  React.useEffect(() => {
    async function loadTemplates() {
      const pageTemplates = await config.api.page_type.listPageTypes(
        token,
        parentType
      );
      pageTemplates
        .map((tpls: PartialPageType[]) => setTemplates(tpls))
        .mapErr((err: ApiError) => setError(err));
      setIsLoading(false);
    }
    loadTemplates();
    return () => {
      setIsLoading(true);
      setError(null);
      setTemplates([]);
    };
  }, [parentType]);

  React.useEffect(() => {
    async function loadPage() {
      if (parentPath) {
        const page = await config.api.page.showPage(token, parentPath || "");
        // console.log(page)
        page
          .map((page: Page) => setParentPage(page))
          .mapErr((err: ApiError) => setError(err));
      } else {
        setParentPage({ meta: { path: "", type: "", breadcrumb: [] } });
      }
    }
    loadPage();
    return () => {
      setParentPage(null);
      setError(null);
    };
  }, [parentPath]);

  return (
    <Container>
      {
        <>
          <Heading>Choose A Type Of Page</Heading>
          {parentPage && (
            <PageBreadcrumb page={parentPage} title="type of template" />
          )}
          <Box paddingLeft={15}>
            <ApiErrorUI error={error} />
            <PageTypesTable
              pageTypes={pageTypes}
              parentPath={parentPath}
              isLoading={isLoading}
            />
          </Box>
        </>
      }
    </Container>
  );
};
