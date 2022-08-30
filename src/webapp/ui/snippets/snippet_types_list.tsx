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
import { Snippet, PartialSnippetType } from "../../casualcms/domain/model";
import { ApiError } from "../../casualcms/domain/ports";
import { AppContext } from "../../config";

import { useAuth } from "../login/hooks";
import { Link, useSearchParams } from "react-router-dom";
import { ChevronRightIcon } from "@chakra-ui/icons";
import { Loader } from "../layout/loader";
import { ApiErrorUI } from "../layout/error_api";
import { SnippetBreadcrumb } from "../layout/breadcrumb";

type SnippetTypesTableProps = {
  isLoading: boolean;
  snippetTypes: PartialSnippetType[];
};
export const SnippetTypesTable: React.FunctionComponent<
  SnippetTypesTableProps
> = (props: SnippetTypesTableProps) => {
  if (props.isLoading) {
    return <Loader label="loading snippet types..." />;
  }

  const snippetTypes = props.snippetTypes;
  return (
    <TableContainer>
      <Table variant="simple">
        <Thead>
          <Tr>
            <Th>Snippet Type</Th>
          </Tr>
        </Thead>
        <Tbody>
          {snippetTypes.map((typ, i) => (
            <Tr key={i}>
              <Td>
                <Link to={`/admin/snippets/new/${typ.type}`}>
                  <Icon as={ChevronRightIcon} w={6} h={6} />
                  {typ.type}
                </Link>
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </TableContainer>
  );
};

export const SnippetTypeList: React.FunctionComponent<{}> = () => {
  const config = React.useContext(AppContext);
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [snippetTypes, setSnippetTypes] = React.useState<PartialSnippetType[]>(
    []
  );
  const [error, setError] = React.useState<ApiError>(null);

  React.useEffect(() => {
    async function loadTypes() {
      const snippetTemplates = await config.api.snippetType.listSnippetTypes(
        token
      );
      snippetTemplates
        .map((tpls: PartialSnippetType[]) => setSnippetTypes(tpls))
        .mapErr((err: ApiError) => setError(err));
      setIsLoading(false);
    }
    loadTypes();
    return () => {
      setIsLoading(true);
      setError(null);
      setSnippetTypes([]);
    };
  }, []);

  return (
    <Container>
      {
        <>
          <Heading>Choose A Type Of Snippet</Heading>
          <SnippetBreadcrumb title="Choose type" />
          <Box paddingLeft={15}>
            <ApiErrorUI error={error} />
            <SnippetTypesTable
              snippetTypes={snippetTypes}
              isLoading={isLoading}
            />
          </Box>
        </>
      }
    </Container>
  );
};
